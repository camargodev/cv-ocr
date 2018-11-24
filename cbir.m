function [charArray, dists] = cbir(absoluteInputImg, baseImagesFolder, N)
    
    S = dir(fullfile(baseImagesFolder, '*.png'));
    dists(1:N) = -1;
    names = strings(N);
    I = normalizeImgSize(imread(absoluteInputImg));
    %disp(baseimg);
    
    for i = 1:numel(S)
        curretimg = fullfile(baseImagesFolder, S(i).name);
        %disp(S(i))
        J = imread(curretimg);
        %imshow(J);
        %pause;
        distance = caller(I, J);
        [dists, names] = add(dists, names, distance, curretimg, N);
    end
    
    %fprintf('As %i imagens mais similares a %s são (aperte qualquer tecla para ver a imagem seguinte):', N, baseimg);
    for i = 1:N
        %fprintf('\n  %iº lugar = %s (Distancia = %f)', i, names(i), dists(i));
        img = imread(char(names(i)));
        %imshow(img);
        %pause;
    end
    %fprintf('\n');
	
	%passo abaixo é necessário pois não é possível passar strings do matlab para python; arrays 1D de caracteres, por outro lado, são permitidos
	charArray = {};
	[~, rows] = size(names);
	for i = 1:rows
		charArray = [charArray, char(names(i))];
	end
end

function J = normalizeImgSize(I)
    normalSize = 200;
    [w, h, d] = size(I);
    remainingW = normalSize-w;
    remainingH = normalSize-h;
    if mod(remainingW,2) == 0
        leftSpace = remainingW/2;
    else
        leftSpace = fix(remainigW/2);
    end
    if mod(remainingH,2) == 0
        upperSpace = remainingH/2;
    else
        upperSpace = fix(remainigH/2);
    end
    J = ones(normalSize, normalSize, d);
    J(leftSpace:leftSpace+w-1, upperSpace:upperSpace+h-1, :) = I;
end

function [dists, names] = add(dists, names, newdist, newname, N)
    position = -1;
    for i = 1:N       
        if (newdist < dists(i) || dists(i) == -1)
            position = i;
            break;
        end
    end
    if (position ~= -1)
        if (position == 1)
            dists = [newdist dists(1:(N-1))];
            names = [newname names(1:(N-1))];
        elseif (position == N)
            dists = [dists(1:(N-1)) newdist];
            names = [names(1:(N-1)) newname];
        else
            dists = [dists(1:(position-1)) newdist dists(position:(N-1))];
            names = [names(1:(position-1)) newname names(position:(N-1))];
        end
    end
end

function J = read(img)
    I = imread(img);
    J = rotateByOrientation(I);
end

function R = rotateByOrientation(I)
   labeled = bwlabel(I);
   measurements = regionprops(labeled, 'Orientation');
   s = ceil(size(I)/2);
   pad = padarray(I, s(1:2), 'replicate', 'both');
   Raux = imrotate(pad, -measurements(1).Orientation);
   S = ceil(size(Raux)/2);
   R = Raux(S(1)-s(1):S(1)+s(1)-1, S(2)-s(2):S(2)+s(2)-1, :);
end

function distance = caller(I, J)
    distance = euclideanDistance(I, J, 0, 1);
    %bbox(img);
    %relativeArea(img);
    %area(img);
    %perimeter(img);
end

function [counter] = area(I)
    counter = 0;
    [lines, columns] = size(I);
    for i = 1:lines
        for j = 1:columns
            if I(i, j) < 255
                counter = counter + 1;
            end
        end
    end   
    %disp('Meaningful pixels: ');
    %disp(counter);
end

function relative = relativeArea(I)
    counter = 0;
    [lines, columns] = size(I);
    pixels = lines * columns;
    for i = 1:lines
        for j = 1:columns
            if I(i, j) < 255
                counter = counter + 1;
            end
        end
    end   
    relative = (counter*100)/pixels;
    %disp('Percentage of meaningful pixels: ');
    %disp(relative);
end

function [counter] = perimeter(I)
    [lines, columns, dims] = size(I);
    counter = area(I);
    resized = zeros(lines+2, columns+2, dims);
    resized(2:end-1,2:end-1,:) = I;
    
    for i = 2:lines
        for j = 2:columns
            if resized(i-1, j-1) < 255 %inferior esquerdo 
                if resized(i, j-1) < 255 %esquerda
                    if resized(i+1, j-1) < 255 %superior esquerdo
                        if resized(i+1, j) < 255 %acima
                            if resized(i+1, j+1) < 255 %superior direita
                                if resized(i, j+1) < 255 %direita
                                    if resized(i-1, j+1) < 255 %inferior direita
                                        if resized(i-1, j) < 255 %abaixo
                                            counter = counter - 1;
                                        end
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    %disp('Perimeter: ');
    %disp(counter);
end

function [width, height, area] = bbox(I)
    [lines, columns] = size(I);    
    maxI = 1; % pixel significativo mais abaixo
    minI = lines; % pixel significativo mais acima
    maxJ = 0; % pixel significativo mais à direita
    minJ = columns; % pixel significativo mais à esquerda
    
    for i = 1:lines
        for j = 1:columns
            if I(i, j) < 255
                if i > maxI
                    maxI = i;
                end
                if i < minI
                    minI = i;
                end
                if j > maxJ
                    maxJ = j;
                end
                if j < minJ
                    minJ = j;
                end
            end
        end
    end
    height = maxI - minI;
    width = maxJ - minJ;
    area = height * width;
    %disp('Bounding box:')
    %fprintf('\tPonto mais inferior: %d\n',maxI );
    %fprintf('\tPonto mais superior: %d\n', minI);
    %fprintf('\tPonto mais à esquerda: %d\n', minJ);
    %fprintf('\tPonto mais à direita: %d\n', maxJ);
    %fprintf('\tLargura: %d\n', width);
    %fprintf('\tAltura: %d\n', height);
    %fprintf('\tÁrea: %d\n\n', area);
end

function [distance] = euclideanDistance(I1, I2, relativeOrNormalArea, bboxWeight)
    %disp('Chamado uma vez');
    %imshow(I2);
    area_1 = area(I1);
    area_2 = area(I2);
    perimeter_1 = perimeter(I1);
    perimeter_2 = perimeter(I2);
    [width_1, height_1, bbarea_1] = bbox(I1);
    [width_2, height_2, bbarea_2] = bbox(I2);
    
    %disp('Área:')
    %fprintf('\tOriginal: %f  Outra: %f\n', area_1, area_2);
    %disp('Perimetro:')
    %fprintf('\tOriginal: %f  Outra: %f\n', perimeter_1, perimeter_2);
    %disp('BBOX largura:')
    %fprintf('\tOriginal: %f  Outra: %f\n', width_1, width_2);
    %disp('BBOX altura:')
    %fprintf('\tOriginal: %f  Outra: %f\n\n', height_1, height_2);
    
    %Cálculo do extent:
    extent_1 = area_1/(height_1*width_1);
    extent_2 = area_2/(height_2*width_2);
    
    %Área do círculo que contem a bounding box
    circ_radius_1 = sqrt(width_1^2 + height_1^2)/2;
    circ_1 = pi*(circ_radius_1^2);
    circ_radius_2 = sqrt(width_2^2 + height_2^2)/2;
    circ_2 = pi*(circ_radius_2^2);
    
    %Circularity:
    area_circ_1 = (perimeter_1^2)/(4*pi);
    area_circ_2 = (perimeter_1^2)/(4*pi);
    circularity_1 = area_1/area_circ_1;
    circularity_2 = area_2/area_circ_2;
        
    
    %Eccentricity:
    I1_inverse_copy = im2bw(I1, 0.0001);
    I1_inverse = I1_inverse_copy;
    I1_inverse(I1_inverse_copy == 1) = 0;
    I1_inverse(I1_inverse_copy == 0) = 1;
    eccentricity_11 = regionprops(I1_inverse,'eccentricity');
    eccentricity_1 = eccentricity_11.Eccentricity;
    
    I2_inverse_copy = im2bw(I2, 0.0001);
    I2_inverse = I2_inverse_copy;
    I2_inverse(I2_inverse_copy == 1) = 0;
    I2_inverse(I2_inverse_copy == 0) = 1;
    eccentricity_22 = regionprops(I2_inverse,'eccentricity');
    eccentricity_2 = eccentricity_22.Eccentricity;
    
    
    fill = regionprops(I1_inverse, 'FilledImage');
    I1_inverse = fill.FilledImage;    
    fill = regionprops(I2_inverse, 'FilledImage');
    I2_inverse = fill.FilledImage;
    
    %Convex hull points:
    convex_points_1_struct = regionprops(I1_inverse, 'ConvexHull');
    [convex_points_1, ~] = size(convex_points_1_struct.ConvexHull);
    convex_points_2_struct = regionprops(I2_inverse, 'ConvexHull');
    [convex_points_2, ~] = size(convex_points_2_struct.ConvexHull);
    
    %Convex hull area:
    convex_area_1_struct = regionprops(I1_inverse, 'ConvexArea');
    convex_area_1 = convex_area_1_struct.ConvexArea;
    convex_area_2_struct = regionprops(I2_inverse, 'ConvexArea');
    convex_area_2 = convex_area_2_struct.ConvexArea;
    
    %Normalização:
    %maxValue = max([area_1, width_1, height_1, perimeter_1, circularity_1, extent_1]);
    maxValue = max([area_1, perimeter_1, circularity_1, extent_1, eccentricity_1, convex_points_1, convex_area_1, area_2, perimeter_2, circularity_2, extent_2, eccentricity_2, convex_points_2, convex_area_2]);
    areaMultiplier = max([area_1, area_2]);
    widthMultiplier = max([width_1, width_2]);
    heightMultiplier = max([height_1, height_2]);
    perimeterMultiplier = max([perimeter_1, perimeter_2]);
    extentMultiplier = max([extent_1, extent_2]);
    circMultiplier = max([circ_1, circ_2]);
    circularityMultiplier = max([circularity_1, circularity_2]);
    eccentricityMultiplier = max([eccentricity_1, eccentricity_2]);
    convexPointsMultiplier = max([convex_points_1, convex_points_2]);
    convexAreaMultiplier = max([convex_area_1, convex_area_2]);
    
    area_1 = (maxValue/areaMultiplier) * area_1;
    area_2 = (maxValue/areaMultiplier) * area_2;
    width_1 = (maxValue/widthMultiplier) * width_1;
    width_2 = (maxValue/widthMultiplier) * width_2;
    height_1 = (maxValue/heightMultiplier) * height_1;
    height_2 = (maxValue/heightMultiplier) * height_2;    
    perimeter_1 = (maxValue/perimeterMultiplier) * perimeter_1; 
    perimeter_2 = (maxValue/perimeterMultiplier) * perimeter_2;
    extent_1 = (maxValue/extentMultiplier) * extent_1;
    extent_2 = (maxValue/extentMultiplier) * extent_2;
    circ_1 = (maxValue/circMultiplier) * circ_1;
    circ_2 = (maxValue/circMultiplier) * circ_2;
    circularity_1 = (maxValue/circularityMultiplier) * circularity_1;
    circularity_2 = (maxValue/circularityMultiplier) * circularity_2;
    eccentricity_1 = (maxValue/eccentricityMultiplier) * eccentricity_1;
    eccentricity_2 = (maxValue/eccentricityMultiplier) * eccentricity_2;
    convex_points_1 = (maxValue/convexPointsMultiplier) * convex_points_1;
    convex_points_2 = (maxValue/convexPointsMultiplier) * convex_points_2;
    convex_area_1 = (maxValue/convexAreaMultiplier) * convex_area_1;
    convex_area_2 = (maxValue/convexAreaMultiplier) * convex_area_2;
    
    if relativeOrNormalArea == 0
        area = (area_1 - area_2)^2;
    else
        area = (relativeArea(I1) - relativeArea(I2))^2;
    end
    perimeter = (perimeter_1 - perimeter_2)^2;
    
    bboxArea = (bbarea_1 - bbarea_2)^2;
    bboxWidth = (width_1 - width_2)^2;
    bboxHeight = (height_1 - height_2)^2;
    extent = (extent_1 - extent_2)^2;
    circ = (circ_1 - circ_2)^2;
    circularity = (circularity_1 - circularity_2)^2;
    eccentricity = (eccentricity_1 - eccentricity_2)^2;
    convexPoints = (convex_points_1 - convex_points_2)^2;
    convexArea = (convex_area_1 - convex_area_2)^2;
    
    
    %disp('Após normalização:')
    %fprintf('\n');
    %disp('Área:')
    %fprintf('\tOriginal: %f  Outra: %f\n', area_1, area_2);
    %disp('Perimetro:')
    %fprintf('\tOriginal: %f  Outra: %f\n', perimeter_1, perimeter_2);
    %disp('BBOX largura:')
    %fprintf('\tOriginal: %f  Outra: %f\n', width_1, width_2);
    %disp('BBOX altura:')
    %fprintf('\tOriginal: %f  Outra: %f\n', height_1, height_2);
    %distance = sqrt(area + perimeter + circ + circularity + bboxHeight + bboxWidth + extent);
    %disp('Extent:')
    %fprintf('\tOriginal: %f  Outra: %f\n', extent_1, extent_2);
    %disp('Circularity:')
    %fprintf('\tOriginal: %f  Outra: %f\n', circularity_1, circularity_2);
    distance = sqrt(area + circularity + perimeter + eccentricity + convexArea + extent + convexPoints);
    %disp('Distancia:')
    %fprintf('%f\n', distance);
    %disp('----------------------')
end